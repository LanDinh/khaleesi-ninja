"""Site registry."""

# Python.
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, TypeVar

# Django.
from django.core.cache import caches
from django.db import models

# gRPC.
from google.protobuf.internal.containers import RepeatedCompositeFieldContainer

# khaleesi.ninja.
from khaleesi.core.logging.textLogger import LOGGER
from khaleesi.proto.core_pb2 import GrpcCallerDetails
from khaleesi.proto.core_sawmill_pb2 import AppCallData, CallData


class SiteRegistrySite(models.Model):
  """Sites."""
  name = models.TextField(unique = True)

  objects: models.Manager[SiteRegistrySite]


class SiteRegistryApp(models.Model):
  """Apps."""
  name = models.TextField()
  site = models.ForeignKey(
    SiteRegistrySite,
    on_delete    = models.CASCADE,
    related_name = 'apps',
  )

  objects: models.Manager[SiteRegistryApp]

  class Meta:
    constraints = [ models.UniqueConstraint(
      fields = [ 'name', 'site' ],
      name   = 'uniqueApp',
    )]


class SiteRegistryService(models.Model):
  """Services."""
  name    = models.TextField()
  app = models.ForeignKey(
    SiteRegistryApp,
    on_delete    = models.CASCADE,
    related_name = 'services',
  )

  objects: models.Manager[SiteRegistryService]

  class Meta:
    constraints = [ models.UniqueConstraint(
      fields = [ 'name', 'app' ],
      name   = 'uniqueService',
    )]


class SiteRegistryMethod(models.Model):
  """Methods."""
  name    = models.TextField()
  service = models.ForeignKey(
    SiteRegistryService,
    on_delete    = models.CASCADE,
    related_name = 'methods',
  )

  objects: models.Manager[SiteRegistryMethod]

  class Meta:
    constraints = [ models.UniqueConstraint(
      fields = [ 'name', 'service' ],
      name   = 'uniqueMethod',
    )]


class SiteRegistryCall(models.Model):
  """Map calls."""
  caller = models.ForeignKey(
    SiteRegistryMethod,
    on_delete    = models.CASCADE,
    related_name = 'calledBy',
  )
  called = models.ForeignKey(
    SiteRegistryMethod,
    on_delete    = models.CASCADE,
    related_name = 'calls',
  )

  objects: models.Manager[SiteRegistryCall]

  class Meta:
    constraints = [ models.UniqueConstraint(fields = [ 'caller', 'called' ], name = 'uniqueCalls')]


T = TypeVar('T')


@dataclass
class Site:
  """Simple representation of the sites."""
  apps : Dict[str, App] = field(default_factory = dict)

@dataclass
class App:
  """Simple representation of the apps."""
  services : Dict[str, Service] = field(default_factory = dict)

@dataclass
class Service:
  """Simple representation of the grpc services."""
  methods : Dict[str, Method] = field(default_factory = dict)

@dataclass
class Method:
  """Simple representation of the grpc methods."""
  calls   : Dict[str, Site] = field(default_factory = dict)
  calledBy: Dict[str, Site] = field(default_factory = dict)


class SiteRegistry:
  """Site registry."""

  cache = caches['site-registry']

  def addCall(self, *, callerDetails: GrpcCallerDetails, calledDetails: GrpcCallerDetails) -> None :
    """If the call is not yet in the siteRegistry, add it."""
    if self._shouldExitEarly(callerDetails = callerDetails):
      return
    if self._shouldExitEarly(callerDetails = calledDetails):
      return

    siteRegistry = self.getSiteRegistry()

    shouldAddCaller = self._shouldAddSiteRegistryEntry(
      siteRegistry  = siteRegistry,
      callerDetails = callerDetails,
    )
    shouldAddCalled = self._shouldAddSiteRegistryEntry(
      siteRegistry  = siteRegistry,
      callerDetails = calledDetails,
    )

    # If either the caller or the called was added, we always have to add the call, too.
    shouldAddCall = shouldAddCaller or shouldAddCalled
    # If neither the caller nor the called was added, we need to check if the call should be added.
    if not shouldAddCall:
      site          = siteRegistry[callerDetails.site]
      app           = site.apps[callerDetails.app]
      service       = app.services[callerDetails.service]
      method        = service.methods[callerDetails.method]
      shouldAddCall = self._shouldAddSiteRegistryEntry(
          siteRegistry  = method.calls,
          callerDetails = calledDetails,
      )
    if shouldAddCall:
      caller = self._getOrCreateEntryForDb(callerDetails = callerDetails)
      called = self._getOrCreateEntryForDb(callerDetails = calledDetails)
      SiteRegistryCall.objects.get_or_create(caller_id = caller.pk, called_id = called.pk)
      self.reload()

  def addApp(self, *, callerDetails: GrpcCallerDetails) -> None :
    """If the entry is not yet in the siteRegistry, add it."""
    if self._shouldExitEarly(callerDetails = callerDetails):
      return

    if self._shouldAddSiteRegistryEntry(
        siteRegistry  = self.getSiteRegistry(),
        callerDetails = callerDetails,
    ):
      self._getOrCreateEntryForDb(callerDetails = callerDetails)
      self.reload()

  def _shouldExitEarly(self, *, callerDetails: GrpcCallerDetails) -> bool :
    return not (
        callerDetails.site and callerDetails.app
        and callerDetails.service and callerDetails.method
    )

  def _shouldAddSiteRegistryEntry(
      self, *,
      siteRegistry : Dict[str, Site],
      callerDetails: GrpcCallerDetails,
  ) -> bool :
    site = siteRegistry.get(callerDetails.site, None)
    if not site:
      return True

    app = site.apps.get(callerDetails.app, None)
    if not app:
      return True

    service = app.services.get(callerDetails.service, None)
    if not service:
      return True

    method = service.methods.get(callerDetails.method, None)
    if not method:
      return True

    return False


  def reload(self) -> None :
    """Reload the site registry from the DB."""
    calls = SiteRegistryCall.objects.all().select_related(
      'caller__service__app__site',
      'called__service__app__site',
    )
    methods = SiteRegistryMethod.objects.all().select_related('service__app__site')
    siteRegistry: Dict[str, Site] = {}

    # There might be some methods without calls, so add them first.
    for method in methods:
      self._reloadMethod(siteRegistry = siteRegistry, method = method)

    for call in calls:
      caller = self._reloadMethod(siteRegistry = siteRegistry, method = call.caller)
      called = self._reloadMethod(siteRegistry = siteRegistry, method = call.called)
      self._reloadMethod(siteRegistry = caller.calls   , method = call.called)
      self._reloadMethod(siteRegistry = called.calledBy, method = call.caller)

    self.cache.clear()
    self.cache.set('site-registry', siteRegistry)

    LOGGER.debug(f'Site registry reloaded: {len(methods)} entries, {len(calls)} calls')

  def getCallData(self, *, owner: GrpcCallerDetails) -> AppCallData :
    """Get call data for the affected app."""
    appCallData = AppCallData()
    self.addApp(callerDetails = owner)
    ownApp = self.getSiteRegistry()[owner.site].apps[owner.app]

    for serviceName, service in ownApp.services.items():
      for methodName, method in service.methods.items():
        callData = CallData()
        callData.call.site    = owner.site
        callData.call.app     = owner.app
        callData.call.service = serviceName
        callData.call.method  = methodName
        self._addDataToCall(fullList = method.calls   , resultList = callData.calls)
        self._addDataToCall(fullList = method.calledBy, resultList = callData.calledBy)
        appCallData.callList.append(callData)

    return appCallData

  def _addDataToCall(
      self, *,
      fullList  : Dict[str, Site],
      resultList: RepeatedCompositeFieldContainer[GrpcCallerDetails],
  ) -> None :
    for siteName, site in fullList.items():
      for appName, app in site.apps.items():
        for serviceName, service in app.services.items():
          for methodName, _ in service.methods.items():
            called = GrpcCallerDetails()
            called.site    = siteName
            called.app     = appName
            called.service = serviceName
            called.method  = methodName
            resultList.append(called)

  def _reloadMethod(
      self, *,
      siteRegistry: Dict[str, Site],
      method      : SiteRegistryMethod,
  ) -> Method :
    site = self._getOrCreateDictEntry(
      data  = siteRegistry,
      key   = method.service.app.site.name,
      value = Site()
    )
    app = self._getOrCreateDictEntry(
      data  = site.apps,
      key   = method.service.app.name,
      value = App()
    )
    service = self._getOrCreateDictEntry(
      data  = app.services,
      key   = method.service.name,
      value = Service()
    )
    return self._getOrCreateDictEntry(
      data  = service.methods,
      key   = method.name,
      value = Method()
    )


  def getSiteRegistry(self) -> Dict[str, Site] :
    """Get the site registry."""
    siteRegistry: Dict[str, Site] = self.cache.get('site-registry')
    if not siteRegistry:
      siteRegistry = {}
      self.cache.set('site-registry', siteRegistry)
    return siteRegistry

  def _getOrCreateDictEntry(self, *, data: Dict[str, T], key: str, value: T) -> T :
    if not key in data:
      data[key] = value
    return data[key]

  def _getOrCreateEntryForDb(
      self, *,
      callerDetails: GrpcCallerDetails,
  ) -> SiteRegistryMethod :
    LOGGER.debug(
      'Add new site registry entry: '
      f'{callerDetails.site} {callerDetails.app} '
      f'{callerDetails.service} {callerDetails.method}')

    site, _ = SiteRegistrySite.objects.get_or_create(name = callerDetails.site)
    app,  _ = SiteRegistryApp.objects.get_or_create(name = callerDetails.app, site_id = site.pk)
    service, _ = SiteRegistryService.objects.get_or_create(
      name   = callerDetails.service,
      app_id = app.pk,
    )
    method, _ = SiteRegistryMethod.objects.get_or_create(
      name       = callerDetails.method,
      service_id = service.pk,
    )
    return method


SITE_REGISTRY = SiteRegistry()

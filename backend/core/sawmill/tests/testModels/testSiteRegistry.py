"""Test the site registry."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import TransactionTestCase
from khaleesi.proto.core_pb2 import GrpcCallerDetails
from microservice.models.siteRegistry import (
  SITE_REGISTRY,
  SiteRegistrySite,
  SiteRegistryApp,
  SiteRegistryService,
  SiteRegistryMethod,
  SiteRegistryCall,
)


# noinspection DuplicatedCode
@patch('microservice.models.siteRegistry.LOGGER')
class SiteRegistryTestCase(TransactionTestCase):
  """Test the site registry."""

  fixtures = [ 'testSiteRegistry.json' ]

  def testAddingSite(self, *_: MagicMock) -> None :
    """Test adding new services to the registry."""
    # Prepare data.
    callerDetails = GrpcCallerDetails()
    callerDetails.site    = 'new-site'
    callerDetails.app     = 'new-app'
    callerDetails.service = 'new-service'
    callerDetails.method  = 'new-method'
    siteCount    = SiteRegistrySite.objects.count()
    appCount     = SiteRegistryApp.objects.count()
    serviceCount = SiteRegistryService.objects.count()
    methodCount  = SiteRegistryMethod.objects.count()
    SITE_REGISTRY.reload()
    # Execute test.
    SITE_REGISTRY.addApp(callerDetails = callerDetails)
    # Assert result.
    self.assertEqual(siteCount    + 1, SiteRegistrySite.objects.count())
    self.assertEqual(appCount     + 1, SiteRegistryApp.objects.count())
    self.assertEqual(serviceCount + 1, SiteRegistryService.objects.count())
    self.assertEqual(methodCount  + 1, SiteRegistryMethod.objects.count())
    SiteRegistrySite.objects.get(name = callerDetails.site)
    SiteRegistryApp.objects.get(name = callerDetails.app)
    SiteRegistryService.objects.get(name = callerDetails.service)
    SiteRegistryMethod.objects.get(name = callerDetails.method)

  def testAddingApp(self, *_: MagicMock) -> None :
    """Test adding new services to the registry."""
    # Prepare data.
    callerDetails = GrpcCallerDetails()
    callerDetails.site    = 'site-1'
    callerDetails.app     = 'new-app'
    callerDetails.service = 'new-service'
    callerDetails.method  = 'new-method'
    siteCount    = SiteRegistrySite.objects.count()
    appCount     = SiteRegistryApp.objects.count()
    serviceCount = SiteRegistryService.objects.count()
    methodCount  = SiteRegistryMethod.objects.count()
    SITE_REGISTRY.reload()
    # Execute test.
    SITE_REGISTRY.addApp(callerDetails = callerDetails)
    # Assert result.
    self.assertEqual(siteCount       , SiteRegistrySite.objects.count())
    self.assertEqual(appCount     + 1, SiteRegistryApp.objects.count())
    self.assertEqual(serviceCount + 1, SiteRegistryService.objects.count())
    self.assertEqual(methodCount  + 1, SiteRegistryMethod.objects.count())
    SiteRegistryApp.objects.get(name = callerDetails.app)
    SiteRegistryService.objects.get(name = callerDetails.service)
    SiteRegistryMethod.objects.get(name = callerDetails.method)

  def testAddingService(self, *_: MagicMock) -> None :
    """Test adding new services to the registry."""
    # Prepare data.
    callerDetails = GrpcCallerDetails()
    callerDetails.site    = 'site-1'
    callerDetails.app     = 'app-1'
    callerDetails.service = 'new-service'
    callerDetails.method  = 'new-method'
    siteCount    = SiteRegistrySite.objects.count()
    appCount     = SiteRegistryApp.objects.count()
    serviceCount = SiteRegistryService.objects.count()
    methodCount  = SiteRegistryMethod.objects.count()
    SITE_REGISTRY.reload()
    # Execute test.
    SITE_REGISTRY.addApp(callerDetails = callerDetails)
    # Assert result.
    self.assertEqual(siteCount       , SiteRegistrySite.objects.count())
    self.assertEqual(appCount        , SiteRegistryApp.objects.count())
    self.assertEqual(serviceCount + 1, SiteRegistryService.objects.count())
    self.assertEqual(methodCount  + 1, SiteRegistryMethod.objects.count())
    SiteRegistryService.objects.get(name = callerDetails.service)
    SiteRegistryMethod.objects.get( name = callerDetails.method)

  def testAddingMethod(self, *_: MagicMock) -> None :
    """Test adding new services to the registry."""
    # Prepare data.
    callerDetails = GrpcCallerDetails()
    callerDetails.site    = 'site-1'
    callerDetails.app     = 'app-1'
    callerDetails.service = 'service-1'
    callerDetails.method  = 'new-method'
    siteCount    = SiteRegistrySite.objects.count()
    appCount     = SiteRegistryApp.objects.count()
    serviceCount = SiteRegistryService.objects.count()
    methodCount  = SiteRegistryMethod.objects.count()
    SITE_REGISTRY.reload()
    # Execute test.
    SITE_REGISTRY.addApp(callerDetails = callerDetails)
    # Assert result.
    self.assertEqual(siteCount      , SiteRegistrySite.objects.count())
    self.assertEqual(appCount       , SiteRegistryApp.objects.count())
    self.assertEqual(serviceCount   , SiteRegistryService.objects.count())
    self.assertEqual(methodCount + 1, SiteRegistryMethod.objects.count())
    SiteRegistryMethod.objects.get(name = callerDetails.method)

  def testAddCall(self, *_: MagicMock) -> None :
    """Test adding a call."""
    # Prepare data.
    callerDetails = GrpcCallerDetails()
    callerDetails.site    = 'site-1'
    callerDetails.app     = 'app-1'
    callerDetails.service = 'service-1'
    callerDetails.method  = 'method-1'
    calledDetails = GrpcCallerDetails()
    calledDetails.site    = 'site-2'
    calledDetails.app     = 'app-3'
    calledDetails.service = 'service-3'
    calledDetails.method  = 'method-3'
    siteCount    = SiteRegistrySite.objects.count()
    appCount     = SiteRegistryApp.objects.count()
    serviceCount = SiteRegistryService.objects.count()
    methodCount  = SiteRegistryMethod.objects.count()
    callCount    = SiteRegistryCall.objects.count()
    SITE_REGISTRY.reload()
    # Execute test.
    SITE_REGISTRY.addCall(callerDetails = callerDetails, calledDetails = calledDetails)
    # Assert result.
    self.assertEqual(siteCount    , SiteRegistrySite.objects.count())
    self.assertEqual(appCount     , SiteRegistryApp.objects.count())
    self.assertEqual(serviceCount , SiteRegistryService.objects.count())
    self.assertEqual(methodCount  , SiteRegistryMethod.objects.count())
    self.assertEqual(callCount + 1, SiteRegistryCall.objects.count())
    SiteRegistryCall.objects.get(
      caller__name = callerDetails.method,
      called__name = calledDetails.method,
    )

  def testReload(self, *_: MagicMock) -> None :
    """Test reloading the registry."""
    # Execute test.
    SITE_REGISTRY.reload()
    # Assert result.
    for i in range(1, 3):
      self._registryContainsSite(number = i)
    for i in range(1, 4):
      self._registryContainsApp(number = i)
    for i in range(1, 5):
      self._registryContainsService(number = i)
    for i in range(1, 6):
      self._registryContainsMethod(number = i)

    self.assertIn(
      'method-2',
      SITE_REGISTRY.cache.get('site-registry')['site-1'].apps[
        'app-1'
      ].services['service-1'].methods['method-1'].calls['site-2'].apps[
        'app-2'
      ].services['service-2'].methods,
    )

  def testAddAppExitEarly(self, *_: MagicMock) -> None :
    """Test exiting early from adding services."""
    # Prepare data.
    callerDetails = GrpcCallerDetails()
    siteCount    = SiteRegistrySite.objects.count()
    appCount     = SiteRegistryApp.objects.count()
    serviceCount = SiteRegistryService.objects.count()
    methodCount  = SiteRegistryMethod.objects.count()
    SITE_REGISTRY.reload()
    # Execute test.
    SITE_REGISTRY.addApp(callerDetails = callerDetails)
    # Assert result.
    self.assertEqual(siteCount   , SiteRegistrySite.objects.count())
    self.assertEqual(appCount    , SiteRegistryApp.objects.count())
    self.assertEqual(serviceCount, SiteRegistryService.objects.count())
    self.assertEqual(methodCount , SiteRegistryMethod.objects.count())

  def testAddCallExitEarlyCaller(self, *_: MagicMock) -> None :
    """Test exiting early from adding services."""
    # Prepare data.
    callerDetails = GrpcCallerDetails()
    siteCount     = SiteRegistrySite.objects.count()
    appCount      = SiteRegistryApp.objects.count()
    serviceCount  = SiteRegistryService.objects.count()
    methodCount   = SiteRegistryMethod.objects.count()
    SITE_REGISTRY.reload()
    # Execute test.
    SITE_REGISTRY.addCall(callerDetails = callerDetails, calledDetails = callerDetails)
    # Assert result.
    self.assertEqual(siteCount   , SiteRegistrySite.objects.count())
    self.assertEqual(appCount    , SiteRegistryApp.objects.count())
    self.assertEqual(serviceCount, SiteRegistryService.objects.count())
    self.assertEqual(methodCount , SiteRegistryMethod.objects.count())

  def testAddCallExitEarlyCalled(self, *_: MagicMock) -> None :
    """Test exiting early from adding services."""
    # Prepare data.
    callerDetails = GrpcCallerDetails()
    callerDetails.site    = 'site-1'
    callerDetails.app     = 'app-1'
    callerDetails.service = 'service-1'
    callerDetails.method  = 'method-1'
    calledDetails = GrpcCallerDetails()
    siteCount     = SiteRegistrySite.objects.count()
    appCount      = SiteRegistryApp.objects.count()
    serviceCount  = SiteRegistryService.objects.count()
    methodCount   = SiteRegistryMethod.objects.count()
    SITE_REGISTRY.reload()
    # Execute test.
    SITE_REGISTRY.addCall(callerDetails = callerDetails, calledDetails = calledDetails)
    # Assert result.
    self.assertEqual(siteCount   , SiteRegistrySite.objects.count())
    self.assertEqual(appCount    , SiteRegistryApp.objects.count())
    self.assertEqual(serviceCount, SiteRegistryService.objects.count())
    self.assertEqual(methodCount , SiteRegistryMethod.objects.count())

  def testGetCallData(self, *_: MagicMock) -> None :
    """Test fetching the call data for a given khaleesi app."""
    # Prepare data.
    callerDetails = GrpcCallerDetails()
    callerDetails.site    = 'site-1'
    callerDetails.app     = 'app-1'
    callerDetails.service = 'service-1'
    callerDetails.method  = 'method-1'
    calls                 = 'method-2'
    # Execute test.
    result = SITE_REGISTRY.getCallData(owner = callerDetails)
    # Assert result.
    self.assertEqual(1, len(result.callList))
    self.assertEqual(1, len(result.callList[0].calls))
    self.assertEqual(0, len(result.callList[0].calledBy))
    self.assertEqual(callerDetails.method, result.callList[0].call.method)
    self.assertEqual(calls               , result.callList[0].calls[0].method)

  @patch.object(SITE_REGISTRY, 'cache')
  def testGetSiteRegistryNoCache(self, cache: MagicMock, *_: MagicMock) -> None :
    """Test instantiation."""
    # Prepare data.
    cache.get.return_value = None
    # Execute result.
    result = SITE_REGISTRY.getSiteRegistry()
    # Assert result.
    self.assertEqual({}, result)

  def _registryContainsSite(self, *, number: int) -> None :
    self.assertIsNotNone(SITE_REGISTRY.cache.get('site-registry')[f'site-{number}'])

  def _registryContainsApp(self, *, number: int) -> None :
    site = min(number, 2)
    self.assertIn(
      f'app-{number}',
      SITE_REGISTRY.cache.get('site-registry')[f'site-{site}'].apps,
    )

  def _registryContainsService(self, *, number: int) -> None :
    site = min(number, 2)
    app = min(number, 3)
    self.assertIn(
      f'service-{number}',
      SITE_REGISTRY.cache.get('site-registry')[f'site-{site}'].apps[
        f'app-{app}'
      ].services,
    )

  def _registryContainsMethod(self, *, number: int) -> None :
    site = min(number, 2)
    app = min(number, 3)
    service = min(number, 4)
    self.assertIn(
      f'method-{number}',
      SITE_REGISTRY.cache.get('site-registry')[f'site-{site}'].apps[
        f'app-{app}'
      ].services[f'service-{service}'].methods,
    )

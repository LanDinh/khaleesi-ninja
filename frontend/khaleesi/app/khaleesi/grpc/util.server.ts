import { makeGenericClientConstructor, credentials } from '@grpc/grpc-js'
import type * as $protobuf from 'protobufjs'
import { khaleesi } from '../proto/proto'


export class Client<Type extends $protobuf.rpc.Service> {

  site: string
  app: string
  stubName: string
  stub: Type

  constructor(site: string, app: string, stubName: string) {
    this.site = site
    this.app = app
    this.stubName = stubName

    const serviceName = `khaleesi.${site}.${app}.${stubName}`
    const serviceUrl = `${site}-${app}:8000`

    const Channel = makeGenericClientConstructor({}, serviceName)
    const channel = new Channel(serviceUrl, credentials.createInsecure())

    // @ts-ignore
    this.stub = khaleesi[site][app][stubName].create(
      (method: any, requestData: any, callback: any) => channel.makeUnaryRequest(
        `/${serviceName}/${method.name}`,
          arg => arg,
          arg => arg,
        requestData,
        callback,
      )
    )
  }
}

export const Singleton = <Value>(site: string, app: string, valueFactory: () => Value): Value => {
  const g = global as any
  g.__singletons ??= {}
  g.__singletons['grpc'] ??= {}
  g.__singletons['grpc'][site] ??= valueFactory()
  g.__singletons['grpc'][site][app] ??= valueFactory()
  return g.__singletons['grpc'][site][app]
}

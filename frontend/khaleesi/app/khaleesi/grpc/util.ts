import { makeGenericClientConstructor, credentials } from '@grpc/grpc-js'
import type * as $protobuf from 'protobufjs'
import { khaleesi } from '../proto/proto'


export class Client<Type extends $protobuf.rpc.Service> {

  gate: string
  service: string
  stubName: string
  stub: Type

  constructor(gate: string, service: string, stubName: string) {
    this.gate = gate
    this.service = service
    this.stubName = stubName

    const serviceName = `khaleesi.${gate}.${service}.${stubName}`
    const serviceUrl = `${gate}-${service}:8000`

    const Channel = makeGenericClientConstructor({}, serviceName)
    const channel = new Channel(serviceUrl, credentials.createInsecure())

    // @ts-ignore
    this.stub = khaleesi[gate][service][stubName].create(
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

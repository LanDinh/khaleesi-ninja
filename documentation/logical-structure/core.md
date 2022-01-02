# core

This gate contains the common logic shared by all gates.

![Core Structure](/documentation/images/logical-structure/core.svg)

## frontgate

## backgate

## guard

## sawmill

This service is responsible for logging.

![Sawmill Structure](/documentation/images/logical-structure/core-sawmill.svg)

The different types of logs are:

* `Metadata` contains metadata shared by all log types and is inherited from by all log types
* `Event` contains information relating to actions that might require auditing 

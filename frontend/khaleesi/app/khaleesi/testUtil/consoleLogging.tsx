type ConsoleFunction = (data: any[]) => void

export function suppressConsoleFunction(
  errorName      : string,
  originalConsole: ConsoleFunction,
): ConsoleFunction {
  return (message: any[]): void => {
    !message.toString().includes(errorName) && originalConsole(message)
  }
}

export function suppressReactRouterFutureWarnings(
  originalWarning: ConsoleFunction,
): ConsoleFunction {
  return suppressConsoleFunction('React Router Future Flag Warning', originalWarning)
}

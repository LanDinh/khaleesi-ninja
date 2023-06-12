type ConsoleFunction = (data: any[]) => void
export function suppressConsoleFunction(
  errorName      : string,
  originalConsole: ConsoleFunction,
): ConsoleFunction {
  return (message: any[]): void => {
    !message.toString().includes(errorName) && originalConsole(message)
  }
}
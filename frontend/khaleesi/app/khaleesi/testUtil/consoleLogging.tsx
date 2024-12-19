type ConsoleFunction = (data: any[]) => void

export function suppressConsoleFunction(
  errorNames     : string[],
  originalConsole: ConsoleFunction,
): ConsoleFunction {
  return (message: any[]): void => {
    let passed = true
    for (const errorName of errorNames) {
      if (message.toString().includes(errorName)) {
        passed = false
        break
      }
    }
    passed && originalConsole(message)
  }
}

export function suppressReactRouterFutureWarnings(
  originalWarning: ConsoleFunction,
): ConsoleFunction {
  const reactRouterFutureWarnings = [
    'You can use the `v7_startTransition` future flag to opt-in early.',
    'You can use the `v7_relativeSplatPath` future flag to opt-in early.',
    'You can use the `v7_fetcherPersist` future flag to opt-in early.',
    'You can use the `v7_normalizeFormMethod` future flag to opt-in early.',
    'You can use the `v7_partialHydration` future flag to opt-in early.',
    'You can use the `v7_skipActionErrorRevalidation` future flag to opt-in early.',
  ]
  return suppressConsoleFunction(reactRouterFutureWarnings, originalWarning)
}

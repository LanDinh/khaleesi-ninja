import { links, ErrorBoundary, App, handle } from './khaleesi/components/document'


const TestApp: () => JSX.Element = () => <App title="Test App" />
export default TestApp
export { links, ErrorBoundary, handle }

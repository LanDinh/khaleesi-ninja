import { links, ErrorBoundary, App, handle } from './khaleesi/home/document'


const TestApp: () => JSX.Element = () => <App title="Test App" />
export default TestApp
export { links, ErrorBoundary, handle }

import { links, ErrorBoundary, App, handle } from './khaleesi/home/document'
import { loader } from './khaleesi/home/document.server'


const TestApp: () => JSX.Element = () => <App title="Test App" />
export default TestApp
export { links, ErrorBoundary, handle, loader }

import { links, ErrorBoundary, App, handle } from './khaleesi/components/document'
import { topNavigationData } from './khaleesi/navigation/commonNavigationData'


const TestApp = () => <App title="Test App" />
export default TestApp
export { links, ErrorBoundary, handle }
export const navigationProperties = topNavigationData[0]

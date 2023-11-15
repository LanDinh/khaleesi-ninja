import { links, ErrorBoundary, App, handle } from './khaleesi/components/document'
import { topNavigationData } from './khaleesi/navigation/commonNavigationData'


const AdminApp: () => JSX.Element = () => <App title="Admin Console" />
export default AdminApp
export { links, ErrorBoundary, handle }
export const navigationProperties = topNavigationData[0]

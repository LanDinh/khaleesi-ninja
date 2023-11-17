import { links, ErrorBoundary, App, handle } from './khaleesi/home/document'


const AdminApp: () => JSX.Element = () => <App title="Admin Console" />
export default AdminApp
export { links, ErrorBoundary, handle }

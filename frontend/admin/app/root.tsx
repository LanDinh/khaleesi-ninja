import { links, ErrorBoundary, App, handle } from './khaleesi/home/document'
import { loader } from './khaleesi/home/document.server'


const AdminApp: () => JSX.Element = () => <App title="Admin Console" />
export default AdminApp
export { links, ErrorBoundary, handle, loader }

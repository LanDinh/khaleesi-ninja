import { links, ErrorBoundary, App, handle } from './khaleesi/home/document'
import { loader } from './khaleesi/home/document.server'


const NewApp: () => JSX.Element = () => <App title="Lorem Ipsum" />
export default NewApp
export { links, ErrorBoundary, handle, loader }

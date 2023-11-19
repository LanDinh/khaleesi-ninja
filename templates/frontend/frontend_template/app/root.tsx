import { links, ErrorBoundary, App, handle, loader } from './khaleesi/home/document'


const NewApp: () => JSX.Element = () => <App title="Lorem Ipsum" />
export default NewApp
export { links, ErrorBoundary, handle, loader }

import { links, ErrorBoundary, App, handle } from './khaleesi/components/document'
import { topNavigationData } from './khaleesi/navigation/commonNavigationData'


const NewApp: () => JSX.Element = () => <App title="Lorem Ipsum" />
export default NewApp
export { links, ErrorBoundary, handle }
export const navigationProperties = topNavigationData[0]

import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { Table } from '../../../app/khaleesi/components/table/table'
import { createTestingStub } from '../../util/remixStub'


test('Table renders as expected.', async () => {
  // Prepare data.
  type Data = { label: string, id: string }
  const columns = [{ label: 'header', value: (data: Data): string => data.label }]
  const rowId = (data: Data): string => data.id
  const data = [{ label: 'one', id: '1' }, { label: 'two', id: '2' }]
  let RemixStub = createTestingStub(() => <Table<Data>
    columns={columns}
    rowId={rowId}
    data={data}
  />)
  // Execute test.
  render(<RemixStub />)
  // Assert result.
  expect(screen.getByRole('table')).toBeInTheDocument()
  expect(screen.getByText('header')).toBeInTheDocument()
  expect(screen.getByText('one')).toBeInTheDocument()
  expect(screen.getByText('two')).toBeInTheDocument()
})

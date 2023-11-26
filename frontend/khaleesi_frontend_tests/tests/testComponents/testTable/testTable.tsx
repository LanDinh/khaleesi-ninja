import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import {
  Table,
  searchParamAsNumber,
  handleSizeChange,
  handlePageChange,
} from '../../../app/khaleesi/components/table/table'
import { Paginator } from '../../../app/khaleesi/components/table/paginator'
import { createTestingStub } from '../../../app/khaleesi/testUtil/remixStub'
import type { ChangeEvent, MouseEvent } from 'react'
import type { SetURLSearchParams, URLSearchParamsInit } from 'react-router-dom'


jest.mock('../../../app/khaleesi/components/table/paginator')
jest.mock('@remix-run/react', () => ({
  ...jest.requireActual('@remix-run/react'),
  useSearchParams: (): any[] => ([ { has: () => false }, jest.fn() ]),
}))


test('Table renders as expected.', () => {
  // Prepare data.
  type Data = { label: string, id: string }
  const columns = [{ label: 'header', value: (data: Data): string => data.label }]
  const rowId = (data: Data): string => data.id
  const data = [{ label: 'one', id: '1' }, { label: 'two', id: '2' }]
  const total = 2
  const mockPaginator = Paginator as jest.MockedFunction<typeof Paginator>
  mockPaginator.mockImplementation(() => <></>)

  let RemixStub = createTestingStub(() => <Table<Data>
    columns={columns}
    rowId={rowId}
    data={data}
    total={total}
  />)
  // Execute test.
  render(<RemixStub />)
  // Assert result.
  expect(screen.getByRole('table')).toBeInTheDocument()
  expect(screen.getByText('header')).toBeInTheDocument()
  expect(screen.getByText('one')).toBeInTheDocument()
  expect(screen.getByText('two')).toBeInTheDocument()
  expect(mockPaginator).toHaveBeenCalled()
})

describe('Helper functions.', () => {
  test('searchParamAsNumber returns correct number.', () => {
    // Prepare data.
    const searchParams = new URLSearchParams()
    const name = 'name'
    const defaultValue = 13
    searchParams.set(name, '42')
    // Execute test.
    const result = searchParamAsNumber(searchParams, name, defaultValue)
    // Assert result.
    expect(result).toBe(42)
  })

  test('searchParamAsNumber returns default value because it is missing.', () => {
    // Prepare data.
    const searchParams = new URLSearchParams()
    const name = 'name'
    const defaultValue = 13
    // Execute test.
    const result = searchParamAsNumber(searchParams, name, defaultValue)
    // Assert result.
    expect(result).toBe(defaultValue)
  })

  test('searchParamAsNumber returns default value because it can\'t be parsed.', () => {
    // Prepare data.
    const searchParams = new URLSearchParams()
    const name = 'name'
    const defaultValue = 13
    searchParams.set(name, 'not a number')
    // Execute test.
    const result = searchParamAsNumber(searchParams, name, defaultValue)
    // Assert result.
    expect(result).toBe(defaultValue)
  })

  test('handleSizeChange', () => {
    // Prepare data.
    const setSearchParams: SetURLSearchParams = (nextInit) => {
      const searchParams = new URLSearchParams()
      const result = (nextInit as (prev: URLSearchParams) => URLSearchParamsInit)(searchParams)
      expect((result as URLSearchParams).get('size')).toBe('13')
    }
    const event = {
      currentTarget: {
        getAttribute: () => 13
      }
    } as unknown as ChangeEvent
    // Execute test & assert result.
    handleSizeChange(setSearchParams)(event)
  })

  test('handlePageChange', () => {
    // Prepare data.
    const setSearchParams: SetURLSearchParams = (nextInit) => {
      const searchParams = new URLSearchParams()
      const result = (nextInit as (prev: URLSearchParams) => URLSearchParamsInit)(searchParams)
      expect((result as URLSearchParams).get('page')).toBe('13')
    }
    const event = {
      currentTarget: {
        getAttribute: () => 13
      }
    } as unknown as MouseEvent
    // Execute test & assert result.
    handlePageChange(setSearchParams)(event)
  })
})

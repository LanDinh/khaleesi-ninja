import type { ChangeEvent, MouseEvent } from 'react'
import { useSearchParams } from '@remix-run/react'
import { Paginator } from './paginator'
import type { TableColumn, DataMapper } from './types'
import type { SetURLSearchParams } from 'react-router-dom'


export const searchParamAsNumber = (
  searchParams: URLSearchParams,
  name        : string,
  defaultValue: number,
): number => {
  if (searchParams.has(name)) {
    return parseInt(searchParams.get(name) || '') || defaultValue
  }
  return defaultValue
}

export const handleSizeChange = (setSearchParams: SetURLSearchParams) => {
  return (event: ChangeEvent): void => {
    setSearchParams((prev: URLSearchParams) => {
      const value = event.currentTarget.getAttribute('value')
      if (null !== value) {
        prev.set('size', value)
      }
      return prev
    })
  }
}

export const handlePageChange = (setSearchParams: SetURLSearchParams) => {
  return (event: MouseEvent): void => {
    setSearchParams((prev: URLSearchParams) => {
      const value = event.currentTarget.getAttribute('value')
      if (null !== value) {
        prev.set('page', value)
      }
      return prev
    })
  }
}

export function Table<Data>(
  { columns, rowId, data, total }: {
    columns: TableColumn<Data>[],
    rowId  : DataMapper<Data>,
    data   : Data[],
    total  : number,
  },
): JSX.Element {
  const [ searchParams, setSearchParams ] = useSearchParams()

  // URL parameters.
  const page = searchParamAsNumber(searchParams, 'page', 1)
  const size = searchParamAsNumber(searchParams, 'size', 5)

  return <table className="khaleesi-table">
    <thead className="khaleesi-table-header"><tr>
      {columns.map(column => <th key={column.label}>{column.label}</th>)}
    </tr></thead>
    <tbody className="khaleesi-table-body">
    {data.map((data: Data) => <tr key={rowId(data)}>
      {columns.map(column => <td key={column.label}>{column.value(data)}</td>)}
    </tr>)}
    </tbody>
    <tfoot><tr><th colSpan={columns.length}>
      <Paginator
        total={total}
        page={page}
        size={size}
        handlePageChange={handlePageChange(setSearchParams)}
        handleSizeChange={handleSizeChange(setSearchParams)}
      />
    </th></tr></tfoot>
  </table>
}

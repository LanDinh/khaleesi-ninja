import { TableColumn, DataMapper } from './types'


export function Table<Data>(
  { columns, rowId, data }: {
    columns: TableColumn<Data>[],
    rowId  : DataMapper<Data>,
    data   : Data[],
  },
): JSX.Element {
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
    </th></tr></tfoot>
  </table>
}

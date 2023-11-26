import type { ChangeEvent, MouseEvent } from 'react'
import { FirstIcon, PreviousIcon, NextIcon, LastIcon } from './icon'


const DEFAULT_SIZES = [ 25, 50, 100 ]

export function Paginator(
  { total, page, size, handleSizeChange, handlePageChange }: {
    total           : number,
    page            : number,
    size            : number,
    handleSizeChange: (event: ChangeEvent) => void,
    handlePageChange: (event: MouseEvent) => void,
  },
): JSX.Element {
  const sizes = new Set([size, ...DEFAULT_SIZES])
  const firstIndex = (page - 1) * size + 1
  const lastIndex = Math.min(page * size, total)
  const minPage = 1
  const maxPage = Math.ceil(total / size)

  return <div className="khaleesi-table-pagination">
    <select defaultValue={size} onChange={handleSizeChange}>
      { [...sizes].map(value => <option value={value} key={value}>{ value }</option>) }
    </select>
    <div>{firstIndex} - {lastIndex} / {total}</div>
    <button
      onClick={handlePageChange}
      value={minPage}
      disabled={minPage === page}
    >
      <FirstIcon />
    </button>
    <button
      onClick={handlePageChange}
      value={Math.max(minPage, page - 1)}
      disabled={minPage === page}
    >
      <PreviousIcon />
    </button>
    <button
      onClick={handlePageChange}
      value={Math.min(maxPage, page + 1)}
      disabled={maxPage === page}
    >
      <NextIcon />
    </button>
    <button
      onClick={handlePageChange}
      value={maxPage}
      disabled={maxPage === page}
    >
      <LastIcon />
    </button>
  </div>
}

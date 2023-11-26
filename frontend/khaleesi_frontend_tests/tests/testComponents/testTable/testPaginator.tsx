import '@testing-library/jest-dom'
import { render, screen, fireEvent } from '@testing-library/react'
import { Paginator } from '../../../app/khaleesi/components/table/paginator'
import { createTestingStub } from '../../util/remixStub'


describe('Rendering.', () => {
  test('Paginator renders as expected.', () => {
    // Prepare data.
    const total = 42
    const page = 7
    const size = 5
    const handleSizeChange = jest.fn()
    const handlePageChange = jest.fn()
    let RemixStub = createTestingStub(() => <Paginator
      total={total}
      page={page}
      size={size}
      handleSizeChange={handleSizeChange}
      handlePageChange={handlePageChange}
    />)
    // Execute test.
    render(<RemixStub/>)
    // Assert result.
    expect(screen.getByRole('option', { name: '5' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: '25' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: '50' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: '100' })).toBeInTheDocument()
    expect(screen.getByText('31 ', { exact: false })).toBeInTheDocument()
    expect(screen.getByText('35 ', { exact: false })).toBeInTheDocument()
    expect(screen.getByText(`/ ${total}`, { exact: false })).toBeInTheDocument()
  })

  test('Paginator renders as expected for the last page and default size.', () => {
    // Prepare data.
    const total = 42
    const page = 2
    const size = 25
    const handleSizeChange = jest.fn()
    const handlePageChange = jest.fn()
    let RemixStub = createTestingStub(() => <Paginator
      total={total}
      page={page}
      size={size}
      handleSizeChange={handleSizeChange}
      handlePageChange={handlePageChange}
    />)
    // Execute test.
    render(<RemixStub/>)
    // Assert result.
    expect(screen.queryByRole('option', { name: '5' })).toBeNull()
    expect(screen.getByRole('option', { name: '25' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: '50' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: '100' })).toBeInTheDocument()
    expect(screen.getByText('26 ', { exact: false })).toBeInTheDocument()
    expect(screen.getByText('42 ', { exact: false })).toBeInTheDocument()
    expect(screen.getByText(`/ ${total}`, { exact: false })).toBeInTheDocument()
  })
})

describe('Size changing', () => {
  test('Changing size works as expected.', async () => {
    // Prepare data.
    const total = 42
    const page = 7
    const size = 5
    const handleSizeChange = jest.fn()
    const handlePageChange = jest.fn()
    let RemixStub = createTestingStub(() => <Paginator
      total={total}
      page={page}
      size={size}
      handleSizeChange={handleSizeChange}
      handlePageChange={handlePageChange}
    />)
    // Execute test.
    const result = render(<RemixStub />)
    fireEvent.change(result.container.querySelectorAll('select')[0], { target: { value: 25 } })
    // Assert result.
    expect(handleSizeChange).toHaveBeenCalled()
    expect(handlePageChange).not.toHaveBeenCalled()
  })
})

describe('Page navigation', () => {
  test('Clicking first page works as expected.', async () => {
    // Prepare data.
    const total = 42
    const page = 7
    const size = 5
    const handleSizeChange = jest.fn()
    const handlePageChange = jest.fn()
    let RemixStub = createTestingStub(() => <Paginator
      total={total}
      page={page}
      size={size}
      handleSizeChange={handleSizeChange}
      handlePageChange={handlePageChange}
    />)
    // Execute test.
    const result = render(<RemixStub/>)
    fireEvent.click(result.container.querySelectorAll('button')[0])
    // Assert result.
    expect(handleSizeChange).not.toHaveBeenCalled()
    expect(handlePageChange).toHaveBeenCalled()
  })

  test('Clicking previous page works as expected.', async () => {
    // Prepare data.
    const total = 42
    const page = 7
    const size = 5
    const handleSizeChange = jest.fn()
    const handlePageChange = jest.fn()
    let RemixStub = createTestingStub(() => <Paginator
      total={total}
      page={page}
      size={size}
      handleSizeChange={handleSizeChange}
      handlePageChange={handlePageChange}
    />)
    // Execute test.
    const result = render(<RemixStub/>)
    fireEvent.click(result.container.querySelectorAll('button')[1])
    // Assert result.
    expect(handleSizeChange).not.toHaveBeenCalled()
    expect(handlePageChange).toHaveBeenCalled()
  })

  test('Clicking next page works as expected.', async () => {
    // Prepare data.
    const total = 42
    const page = 7
    const size = 5
    const handleSizeChange = jest.fn()
    const handlePageChange = jest.fn()
    let RemixStub = createTestingStub(() => <Paginator
      total={total}
      page={page}
      size={size}
      handleSizeChange={handleSizeChange}
      handlePageChange={handlePageChange}
    />)
    // Execute test.
    const result = render(<RemixStub/>)
    fireEvent.click(result.container.querySelectorAll('button')[2])
    // Assert result.
    expect(handleSizeChange).not.toHaveBeenCalled()
    expect(handlePageChange).toHaveBeenCalled()
  })

  test('Clicking last page works as expected.', async () => {
    // Prepare data.
    const total = 42
    const page = 7
    const size = 5
    const handleSizeChange = jest.fn()
    const handlePageChange = jest.fn()
    let RemixStub = createTestingStub(() => <Paginator
      total={total}
      page={page}
      size={size}
      handleSizeChange={handleSizeChange}
      handlePageChange={handlePageChange}
    />)
    // Execute test.
    const result = render(<RemixStub/>)
    fireEvent.click(result.container.querySelectorAll('button')[3])
    // Assert result.
    expect(handleSizeChange).not.toHaveBeenCalled()
    expect(handlePageChange).toHaveBeenCalled()
  })
})

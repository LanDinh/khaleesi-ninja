import '@testing-library/jest-dom'
import { render, screen, fireEvent } from '@testing-library/react'
import { Paginator } from '../../../app/khaleesi/components/table/paginator'
import { createTestingStub } from '../../../app/khaleesi/testUtil/remixStub'


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
    const result = render(<RemixStub/>)
    // Assert result.
    expect(screen.getByRole('option', { name: '5' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: '25' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: '50' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: '100' })).toBeInTheDocument()
    expect(screen.getByText('31 ', { exact: false })).toBeInTheDocument()
    expect(screen.getByText('35 ', { exact: false })).toBeInTheDocument()
    expect(screen.getByText(`/ ${total}`, { exact: false })).toBeInTheDocument()
    expect(result.container.querySelectorAll('button')[0].value).toBe('1')
    expect(result.container.querySelectorAll('button')[1].value).toBe('6')
    expect(result.container.querySelectorAll('button')[2].value).toBe('8')
    expect(result.container.querySelectorAll('button')[3].value).toBe('9')
    expect(result.container.querySelectorAll('button')[0]).not.toBeDisabled()
    expect(result.container.querySelectorAll('button')[1]).not.toBeDisabled()
    expect(result.container.querySelectorAll('button')[2]).not.toBeDisabled()
    expect(result.container.querySelectorAll('button')[3]).not.toBeDisabled()
  })

  test('Paginator renders as expected for the last page', () => {
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
    const result = render(<RemixStub/>)
    // Assert result.
    expect(screen.getByText('26 ', { exact: false })).toBeInTheDocument()
    expect(screen.getByText('42 ', { exact: false })).toBeInTheDocument()
    expect(screen.getByText(`/ ${total}`, { exact: false })).toBeInTheDocument()
    expect(result.container.querySelectorAll('button')[0].value).toBe('1')
    expect(result.container.querySelectorAll('button')[1].value).toBe('1')
    expect(result.container.querySelectorAll('button')[2].value).toBe('2')
    expect(result.container.querySelectorAll('button')[3].value).toBe('2')
    expect(result.container.querySelectorAll('button')[0]).not.toBeDisabled()
    expect(result.container.querySelectorAll('button')[1]).not.toBeDisabled()
    expect(result.container.querySelectorAll('button')[2]).toBeDisabled()
    expect(result.container.querySelectorAll('button')[3]).toBeDisabled()
  })

  test('Paginator renders as expected for a default size.', () => {
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
  })

  test('Paginator renders as expected for the first page.', () => {
    // Prepare data.
    const total = 42
    const page = 1
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
    // Assert result.
    expect(screen.getByRole('option', { name: '5' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: '25' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: '50' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: '100' })).toBeInTheDocument()
    expect(screen.getByText('1 ', { exact: false })).toBeInTheDocument()
    expect(screen.getByText('5 ', { exact: false })).toBeInTheDocument()
    expect(screen.getByText(`/ ${total}`, { exact: false })).toBeInTheDocument()
    expect(result.container.querySelectorAll('button')[0].value).toBe('1')
    expect(result.container.querySelectorAll('button')[1].value).toBe('1')
    expect(result.container.querySelectorAll('button')[2].value).toBe('2')
    expect(result.container.querySelectorAll('button')[3].value).toBe('9')
    expect(result.container.querySelectorAll('button')[0]).toBeDisabled()
    expect(result.container.querySelectorAll('button')[1]).toBeDisabled()
    expect(result.container.querySelectorAll('button')[2]).not.toBeDisabled()
    expect(result.container.querySelectorAll('button')[3]).not.toBeDisabled()
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
    fireEvent.change(result.container.querySelectorAll('select')[0])
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

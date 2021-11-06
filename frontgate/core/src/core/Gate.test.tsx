import React              from 'react'
import { render, screen } from '@testing-library/react'
import Gate               from './Gate'

test('renders learn react link', () => {
  render(<Gate />)
  const linkElement = screen.getByText(/Test/i)
  expect(linkElement).toBeInTheDocument()
})

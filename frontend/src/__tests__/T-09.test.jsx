import { fireEvent, render, screen, waitFor } from '@testing-library/react'

import SlotPicker from '../pages/SlotPicker.jsx'

const mockApi = {
  getSlots: vi.fn(async () => ({
    slots: [
      { id: 1, slotDate: '2026-09-23', startTime: '09:00', packageCode: 'general', remaining: 3 },
      { id: 2, slotDate: '2026-09-23', startTime: '10:00', packageCode: 'general', remaining: 1 },
    ],
  })),
}

vi.mock('../api/client.js', () => ({ api: mockApi }))

test('T-09 แสดงแพ็กเกจและช่วงเวลาว่างพร้อมจำนวนที่นั่งคงเหลือ', async () => {
  render(<SlotPicker />)

  expect(screen.getByText('เลือกแพ็กเกจและช่วงเวลา')).toBeTruthy()
  expect(screen.getByText('แพ็กเกจทั่วไป')).toBeTruthy()

  await waitFor(() => {
    expect(mockApi.getSlots).toHaveBeenCalled()
  })

  await waitFor(() => {
    expect(screen.getByText(/09:00/)).toBeTruthy()
    expect(screen.getByText(/3 ที่นั่งคงเหลือ/)).toBeTruthy()
  })

  fireEvent.click(screen.getByText('แพ็กเกจพิเศษ'))

  await waitFor(() => {
    expect(mockApi.getSlots).toHaveBeenCalledTimes(2)
  })
})

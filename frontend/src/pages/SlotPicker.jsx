import { useEffect, useState } from 'react'

import { api } from '../api/client.js'

const PACKAGE_OPTIONS = [
  { code: 'general', label: 'แพ็กเกจทั่วไป' },
  { code: 'premium', label: 'แพ็กเกจพิเศษ' },
]

export default function SlotPicker() {
  // รองรับ FR-BKG-01, FR-BKG-06
  const [selectedPackage, setSelectedPackage] = useState(PACKAGE_OPTIONS[0].code)
  const [slots, setSlots] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let ignore = false

    async function loadSlots() {
      setLoading(true)
      setError('')

      try {
        const payload = await api.getSlots({
          dateFrom: '2026-09-23',
          packageCode: selectedPackage,
        })

        const nextSlots = Array.isArray(payload?.slots) ? payload.slots : []
        if (!ignore) {
          setSlots(nextSlots)
        }
      } catch (loadError) {
        if (!ignore) {
          setError('ไม่สามารถโหลดช่วงเวลาว่างได้ในขณะนี้')
        }
      } finally {
        if (!ignore) {
          setLoading(false)
        }
      }
    }

    loadSlots()
    return () => {
      ignore = true
    }
  }, [selectedPackage])

  return (
    <section className="mx-auto max-w-3xl rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-2xl font-bold text-slate-800">เลือกแพ็กเกจและช่วงเวลา</h2>
      <p className="mt-2 text-sm text-slate-600">เลือกแพ็กเกจเพื่อดูช่วงเวลาว่างภายใน 30 วันข้างหน้า</p>

      <div className="mt-5 flex flex-wrap gap-3">
        {PACKAGE_OPTIONS.map((option) => (
          <button
            key={option.code}
            type="button"
            onClick={() => setSelectedPackage(option.code)}
            className={[
              'rounded-full border px-4 py-2 text-sm font-medium transition',
              option.code === selectedPackage
                ? 'border-teal-600 bg-teal-600 text-white'
                : 'border-slate-300 bg-white text-slate-700 hover:border-teal-400 hover:text-teal-700',
            ].join(' ')}
          >
            {option.label}
          </button>
        ))}
      </div>

      {error ? <p className="mt-4 text-sm text-red-600">{error}</p> : null}

      <div className="mt-6 space-y-3">
        {loading ? (
          <p className="text-sm text-slate-500">กำลังโหลดช่วงเวลาว่าง...</p>
        ) : slots.length === 0 ? (
          <p className="text-sm text-slate-500">ไม่มีช่วงเวลาว่างสำหรับแพ็กเกจนี้ในขณะนี้</p>
        ) : (
          slots.map((slot) => (
            <button
              key={slot.id}
              type="button"
              className="flex w-full items-center justify-between rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-left transition hover:border-teal-300 hover:bg-teal-50"
            >
              <div>
                <div className="text-sm font-medium text-slate-700">
                  {slot.slotDate || slot.slot_date} • {slot.startTime || slot.start_time}
                </div>
                <div className="text-xs text-slate-500">{slot.packageCode || slot.package_code}</div>
              </div>
              <span className="rounded-full bg-teal-100 px-2.5 py-1 text-sm font-semibold text-teal-700">
                {slot.remaining ?? slot.remaining_count} ที่นั่งคงเหลือ
              </span>
            </button>
          ))
        )}
      </div>
    </section>
  )
}

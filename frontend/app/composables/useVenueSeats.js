export function useVenueSeats(seatsRaw, currentUserId = null) {
  const gapRules = {
    Балкон: {
      7: [{ afterSeatNumber: 13, count: 5 }],
      6: [{ afterSeatNumber: 12, count: 7 }],
      5: [{ afterSeatNumber: 12, count: 7 }],
      4: [{ afterSeatNumber: 12, count: 7 }],
      3: [{ afterSeatNumber: 12, count: 7 }],
      2: [{ afterSeatNumber: 14, count: 3 }],
      1: [{ afterSeatNumber: 14, count: 3 }]
    },
    Амфитеатр: {
      17: [{ afterSeatNumber: 6, count: 2 }, { afterSeatNumber: 20, count: 2 }],
      16: [{ afterSeatNumber: 6, count: 2 }, { afterSeatNumber: 20, count: 2 }],
      15: [{ afterSeatNumber: 6, count: 2 }, { afterSeatNumber: 20, count: 2 }],
      14: [{ afterSeatNumber: 6, count: 2 }, { afterSeatNumber: 20, count: 2 }],
      13: [{ afterSeatNumber: -1, count: 1 }, { afterSeatNumber: 6, count: 2 }, { afterSeatNumber: 11, count: 4 }, { afterSeatNumber: 20, count: 2 }]
    },
    Партер: {
      12: [{ afterSeatNumber: -1, count: 2 }, { afterSeatNumber: 12, count: 2 }],
      11: [{ afterSeatNumber: -1, count: 2 }, { afterSeatNumber: 12, count: 2 }],
      10: [{ afterSeatNumber: -1, count: 2 }, { afterSeatNumber: 12, count: 2 }],
      9: [{ afterSeatNumber: -1, count: 2 }, { afterSeatNumber: 12, count: 2 }],
      8: [{ afterSeatNumber: -1, count: 2 }, { afterSeatNumber: 12, count: 2 }],
      7: [{ afterSeatNumber: -1, count: 2 }, { afterSeatNumber: 12, count: 2 }],
      6: [{ afterSeatNumber: -1, count: 2 }, { afterSeatNumber: 12, count: 2 }],
      5: [{ afterSeatNumber: -1, count: 3 }, { afterSeatNumber: 11, count: 2 }],
      4: [{ afterSeatNumber: -1, count: 3 }, { afterSeatNumber: 11, count: 2 }],
      3: [{ afterSeatNumber: -1, count: 4 }, { afterSeatNumber: 10, count: 2 }],
      2: [{ afterSeatNumber: -1, count: 5 }, { afterSeatNumber: 9, count: 2 }],
      1: [{ afterSeatNumber: -1, count: 6 }, { afterSeatNumber: 8, count: 2 }]
    }
  }

  function isCurrentUserSeat(seat) {
    const resolvedUserId = isRef(currentUserId) ? currentUserId.value : currentUserId
    return resolvedUserId != null && seat.user_id === resolvedUserId
  }

  function seatStatus(seat) {
    if (seat.booking_status === 'available') return 'available'
    if (seat.booking_status === 'unavailable') return 'unavailable'

    if (seat.booking_status === 'held') {
      return isCurrentUserSeat(seat) ? 'held-current' : 'held'
    }

    if (seat.booking_status === 'booked') {
      return isCurrentUserSeat(seat) ? 'booked-current' : 'booked'
    }

    return 'unavailable'
  }

  const groupedSeats = computed(() => {
    const groups = {}

    for (const seat of seatsRaw.value) {
      const section = seat.section ?? 'Default'
      const rowKey = String(seat.row)

      if (!groups[section]) groups[section] = {}
      if (!groups[section][rowKey]) groups[section][rowKey] = []
      groups[section][rowKey].push(seat)
    }

    for (const section of Object.keys(groups)) {
      for (const rowKey of Object.keys(groups[section])) {
        const row = groups[section][rowKey].sort((left, right) => Number(left.number) - Number(right.number))
        const rulesForRow = gapRules[section]?.[Number(rowKey)] ?? []
        const rebuiltRow = []

        const startRule = rulesForRow.find((rule) => Number(rule.afterSeatNumber) === -1)
        if (startRule?.count) {
          for (let i = 0; i < startRule.count; i++) rebuiltRow.push(null)
        }

        for (const seat of row) {
          rebuiltRow.push(seat)

          for (const rule of rulesForRow) {
            if (Number(seat.number) === Number(rule.afterSeatNumber) && rule.count > 0) {
              for (let i = 0; i < rule.count; i++) rebuiltRow.push(null)
            }
          }
        }

        groups[section][rowKey] = rebuiltRow
      }
    }

    const sectionOrder = ['Балкон', 'Амфитеатр', 'Партер']
    const orderedGroups = {}

    for (const section of sectionOrder) {
      if (groups[section]) orderedGroups[section] = groups[section]
    }

    return orderedGroups
  })

  function sortedRowKeys(rowsObj) {
    return Object.keys(rowsObj)
      .map((key) => Number(key))
      .sort((left, right) => right - left)
      .map(String)
  }

  return {
    groupedSeats,
    sortedRowKeys,
    seatStatus,
    isCurrentUserSeat,
  }
}

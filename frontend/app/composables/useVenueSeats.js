// composables/useVenueSeats.js
export function useVenueSeats(seatsRaw, currentUserId = null) {
  const selectedSeats = ref([])

  
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

  // --- Seat helpers ---
  function seatStatus(seat) {
    if (seat.available) return 'available'
    if (!seat.available && seat.user_id != null) return 'booked'
    return 'unavailable'
  }

  function isCurrentUserSeat(seat) {
    return currentUserId != null && seat.user_id === currentUserId
  }
    function toggleSeatSelection(seat) {
    const index = selectedSeats.value.findIndex(s => s.id === seat.id)
    if (index === -1) {
      selectedSeats.value.push(seat)
    } else {
      selectedSeats.value.splice(index, 1)
    }
  }

  

  // --- Group seats by section -> row, insert gaps ---
  const groupedSeats = computed(() => {
  const groups = {}

  for (const s of seatsRaw.value) {
    const section = s.section ?? 'Default'
    const rowKey = String(s.row)
    if (!groups[section]) groups[section] = {}
    if (!groups[section][rowKey]) groups[section][rowKey] = []
    groups[section][rowKey].push(s)
  }

  for (const section of Object.keys(groups)) {
    for (const rowKey of Object.keys(groups[section])) {
      let rowArr = groups[section][rowKey].sort((a, b) => Number(a.number) - Number(b.number))

      // apply gap rules if defined for this section/row
      const rulesForRow = (gapRules[section] && gapRules[section][Number(rowKey)]) || []

      const newRow = []

      // handle start-of-row gaps first
      const startRule = rulesForRow.find(r => Number(r.afterSeatNumber) === -1)
      if (startRule && startRule.count > 0) {
        for (let i = 0; i < startRule.count; i++) newRow.push(null)
      }

      // then add seats and in-row gaps
      for (const seat of rowArr) {
        newRow.push(seat)
        for (const rule of rulesForRow) {
          if (Number(seat.number) === Number(rule.afterSeatNumber) && rule.count > 0) {
            for (let i = 0; i < rule.count; i++) newRow.push(null)
          }
        }
      }

      groups[section][rowKey] = newRow
    }
  }

        // enforce section order
    const sectionOrder = ['Балкон', 'Амфитеатр', 'Партер']
    const orderedGroups = {}
    for (const section of sectionOrder) {
        if (groups[section]) orderedGroups[section] = groups[section]
    }

    return orderedGroups
  })


  function sortedRowKeys(rowsObj) {
    return Object.keys(rowsObj)
      .map(k => Number(k))
      .sort((a, b) => b - a)
      .map(String)
  }

  return {
    groupedSeats,
    sortedRowKeys,
    selectedSeats,
    seatStatus,
    isCurrentUserSeat,
    toggleSeatSelection
  }
}

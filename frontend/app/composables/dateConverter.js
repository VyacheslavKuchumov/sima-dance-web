export function useDateConverter() {
    // Convert ISO (YYYY-MM-DD or full ISO string) → Russian format ("DD.MM.YYYY")
    function isoToRu(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        if (isNaN(date)) return '';
        return date.toLocaleDateString('ru-RU', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        });
    }

    // Convert Russian format ("DD.MM.YYYY") → ISO ("YYYY-MM-DD")
    function ruToIso(russianDate) {
        if (!russianDate) return '';
        const parts = russianDate.split('.');
        if (parts.length !== 3) return '';
        const [day, month, year] = parts.map(p => parseInt(p, 10));
        if (isNaN(day) || isNaN(month) || isNaN(year)) return '';
        // Ensure two-digit day/month
        const dd = String(day).padStart(2, '0');
        const mm = String(month).padStart(2, '0');
        return `${year}-${mm}-${dd}`;
    }

    return {
        isoToRu,
        ruToIso
    };
}
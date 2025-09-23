export function useDateConverter() {
    // This composable converts ISO date strings to Russian date format
    function formatDate(dateString) {
        const options = { year: 'numeric', month: 'long', day: 'numeric', locale: 'ru-RU' };
        return new Date(dateString).toLocaleDateString('ru-RU', options);
    }

    return {
        formatDate
    };
}
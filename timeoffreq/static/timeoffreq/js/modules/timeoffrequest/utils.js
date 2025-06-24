export function formatDateTimeForAPI(datetimeLocalString) {
    if (!datetimeLocalString) return null;

    const date = new Date(datetimeLocalString);
    if (isNaN(date.getTime())) {
        console.error("Invalid date string provided to formatDateTimeForAPI:", datetimeLocalString);
        return null;
    }

    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = '00';

    const offsetMinutes = date.getTimezoneOffset();
    const offsetSign = offsetMinutes > 0 ? '-' : '+';
    const absOffsetMinutes = Math.abs(offsetMinutes);
    const offsetHours = String(Math.floor(absOffsetMinutes / 60)).padStart(2, '0');
    const offsetRemainderMinutes = String(absOffsetMinutes % 60).padStart(2, '0');
    const timezoneOffsetString = `${offsetSign}${offsetHours}:${offsetRemainderMinutes}`;

    return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}${timezoneOffsetString}`;
}
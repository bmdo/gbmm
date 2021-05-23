export interface SortOption {
    id: number,
    friendlyName: string
    field: string
    direction: 'asc' | 'desc'
    active: boolean
}
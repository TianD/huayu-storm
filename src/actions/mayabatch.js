import * as reducerType from '../reducers/reducerType'

export function set_mayabatch_filters(data) {
    return {
        type: reducerType.MAYABATCH_FILTERS,
        data: data
    };
}

export function set_mayabatch_items(data) {
    return {
        type: reducerType.MAYABATCH_ITEMS,
        data: data
    }
}

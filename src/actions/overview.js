import * as reducerType from '../reducers/reducerType'

export function set_overview_filters(data) {
    return {
        type: reducerType.OVERVIEW_FILTERS,
        data: data
    };
}
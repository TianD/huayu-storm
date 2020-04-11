import * as reducerType from '../reducers/reducerType'

export function set_nukebatch_filters(data) {
    return {
        type: reducerType.NUKEBATCH_FILTERS,
        data: data
    };
}

export function set_nukebatch_taskid(data) {
    return {
        type: reducerType.NUKEBATCH_TASKID,
        data: data
    }
}
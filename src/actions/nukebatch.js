import * as reducerType from '../reducers/reducerType'

export function set_nukebatch_project_filters(data) {
    return {
        type: reducerType.NUKEBATCH_PROJECT_FILTERS,
        data: data
    };
}

export function set_nukebatch_shot_filters(data) {
    return {
        type: reducerType.NUKEBATCH_SHOT_FILTERS,
        data: data
    };
}

export function set_nukebatch_taskid(data) {
    return {
        type: reducerType.NUKEBATCH_TASKID,
        data: data
    }
}

export function set_nukebatch_items(data) {
    return {
        type: reducerType.NUKEBATCH_ITEMS,
        data: data
    }
}

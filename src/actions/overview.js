import * as reducerType from '../reducers/reducerType'

export function set_overview_shot_filters(data) {
    return {
        type: reducerType.OVERVIEW_SHOT_FILTERS,
        data: data
    };
}

export function set_overview_project_filters(data) {
    return {
        type: reducerType.OVERVIEW_PROJECT_FILTERS,
        data: data
    };
}
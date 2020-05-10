import * as reducerType from './reducerType';


export function overview_project_filters(state = [], action) {
    switch (action.type) {
        case reducerType.OVERVIEW_PROJECT_FILTERS:
            return action.data

        default:
            return state;
    }
}


export function overview_shot_filters(state = [], action) {
    switch (action.type) {
        case reducerType.OVERVIEW_SHOT_FILTERS:
            return action.data

        default:
            return state;
    }
}

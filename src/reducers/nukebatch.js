import * as reducerType from './reducerType';


export function nukebatch_project_filters(state = [], action) {
    switch (action.type) {
        case reducerType.NUKEBATCH_PROJECT_FILTERS:
            return action.data

        default:
            return state;
    }
}


export function nukebatch_shot_filters(state = [], action) {
    switch (action.type) {
        case reducerType.NUKEBATCH_SHOT_FILTERS:
            return action.data

        default:
            return state;
    }
}


export function nukebatch_taskid(state = 1, action) {
    switch (action.type) {
        case reducerType.NUKEBATCH_TASKID:
            return action.data

        default:
            return state;
    }
}

export function nukebatch_items(state=[], action) {
    switch(action.type) {
        case reducerType.NUKEBATCH_ITEMS:
            return action.data
        default:
            return state;
    }
}
import * as reducerType from './reducerType';


export function nukebatch_filters(state = [], action) {
    switch (action.type) {
        case reducerType.NUKEBATCH_FILTERS:
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
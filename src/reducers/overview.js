import * as reducerType from './reducerType';


export function overview_filters(state = [], action) {
    switch (action.type) {
        case reducerType.OVERVIEW_FILTERS:
            return action.data

        default:
            return state;
    }
}

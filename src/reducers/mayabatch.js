import * as reducerType from './reducerType';


export function mayabatch_filters(state = null, action) {
    switch (action.type) {
        case reducerType.MAYABATCH_FILTERS:
            return action.data

        default:
            return state;
    }
}

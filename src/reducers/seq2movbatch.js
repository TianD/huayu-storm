import * as reducerType from './reducerType';


export function seq2movbatch_filters(state = null, action) {
    switch (action.type) {
        case reducerType.SEQ2MOVBATCH_FILTERS:
            return action.data

        default:
            return state;
    }
}

export function seq2movbatch_items(state=[], action) {
    switch(action.type) {
        case reducerType.SEQ2MOVBATCH_ITEMS:
            return action.data
        default:
            return state;
    }
}
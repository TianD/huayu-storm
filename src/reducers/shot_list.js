import * as reducerType from './reducerType';


export function get_shot_list_failed(state = false, action) {
    switch (action.type) {
        case reducerType.GET_SHOT_LIST_FAILED:
            return action.hasErrored;

        default:
            return state;
    }
}

export function get_shot_list_loading(state = false, action) {
    switch (action.type) {
        case reducerType.GET_SHOT_LIST_LOADING:
            return action.isLoading;

        default:
            return state;
    }
}

export function shot_list(state = [], action) {
    switch (action.type) {
        case reducerType.GET_SHOT_LIST_SUCCESS:
            return action.items;

        default:
            return state;
    }
}
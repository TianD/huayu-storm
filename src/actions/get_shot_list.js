import api from '../api';
import * as reducerType from '../reducers/reducerType'

export function get_shot_list_failed(bool) {
    return {
        type: reducerType.GET_SHOT_LIST_FAILED,
        hasErrored: bool
    };
}

export function get_shot_list_loading(bool) {
    return {
        type: reducerType.GET_SHOT_LIST_LOADING,
        isLoading: bool
    };
}

export function get_shot_list_success(items) {
    return {
        type: reducerType.GET_SHOT_LIST_SUCCESS,
        items
    };
}

export function get_shot_list(project) {
    return (dispatch) => {
        dispatch(get_shot_list_loading(true));
        api.get_shot_list(project)
            .then((response) => {
                if (!response.status === 200) {
                    throw Error(response.statusText);
                }
                dispatch(get_shot_list_loading(false));
                return response;
            })
            .then((response) => dispatch(get_shot_list_success(response.data)))
            .catch(() => dispatch(get_shot_list_failed(true)));
    };
}

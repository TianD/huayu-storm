import api from '../api';
import * as reducerType from '../reducers/reducerType'

export function get_project_list_failed(bool) {
    return {
        type: reducerType.GET_PROJECT_LIST_FAILED,
        hasErrored: bool
    };
}

export function get_project_list_loading(bool) {
    return {
        type: reducerType.GET_PROJECT_LIST_LOADING,
        isLoading: bool
    };
}

export function get_project_list_success(items) {
    return {
        type: reducerType.GET_PROJECT_LIST_SUCCESS,
        items
    };
}

export function get_project_list() {
    return (dispatch) => {
        dispatch(get_project_list_loading(true));
        api.get_project_list()
            .then((response) => {
                if (!response.status === 200) {
                    throw Error(response.statusText);
                }
                dispatch(get_project_list_loading(false));
                return response;
            })
            .then((response) => dispatch(get_project_list_success(response.data)))
            .catch(() => dispatch(get_project_list_failed(true)));
    };
}

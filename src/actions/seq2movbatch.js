import * as reducerType from '../reducers/reducerType'

export function set_seq2movbatch_filters(data) {
    return {
        type: reducerType.SEQ2MOVBATCH_FILTERS,
        data: data
    };
}
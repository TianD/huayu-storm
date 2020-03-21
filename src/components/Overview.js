import React, { Component } from 'react';
import { Cascader, List } from 'antd';
import MyCard from './MyCard';
import DetailView from './DetailView';
import { ModalVisibleContext } from '../context';
import api from '../api'

class Overview extends Component {
    constructor() {
        super()
        this.state = {
            visible: false,
            project_list: null,
            shots: [],
            current_shot: {}
        }
    }

    changeVisible = (flag) => {
        this.setState({
            visible: flag
        })
    }

    onCardClick(item) {
        this.setState({
            current_shot: item
        },
            this.changeVisible(true))
    }

    filterShots = (value) => {
        let project_list = this.state.project_list
        let shot_list;
        if (value.length > 0) {
            let project = project_list.filter((element) => {
                return element["value"] === value[0]
            })[0]
            let episode = project["children"].filter((element) => {
                return element["value"] === value[1]
            })[0]
            if (value[1] === 'all') {
                shot_list = episode["shots"]
            } else {
                let sequence = episode["children"].filter((element) => {
                    return element["value"] === value[2]
                })[0]
                shot_list = sequence["shots"]
            }
        } else {
            shot_list = [];
        }
        this.setState({
            shots: shot_list
        })
    }

    changeProjectList = (value) => {
        this.setState({
            project_list: value
        })
    }

    componentDidMount() {
        api.get_project_list((response) => {
            this.changeProjectList(response.data)
        })
    }

    render() {
        let { visible, project_list, shots, current_shot } = this.state;
        return (
            <ModalVisibleContext.Provider
                value={
                    {
                        visible: visible,
                        project_list: project_list,
                        changeVisible: this.changeVisible,
                        changeProjectList: this.changeProjectList,
                    }
                }>
                <div>
                    <Cascader
                        options={project_list}
                        onChange={(value) => this.filterShots(value)}
                        placeholder="Please select" />
                    <List
                        itemLayout={'horizontal'}
                        dataSource={shots}
                        grid={{ gutter: 360, lg: 6, md: 2, sm: 1, xs: 1 }}
                        column={4}
                        renderItem={
                            item => (
                                <List.Item>
                                    <MyCard shot={item} onClick={(e) => this.onCardClick(item)} />
                                </List.Item>
                            )
                        }
                    >
                    </List>
                    <DetailView shot={current_shot} visible={visible} />
                </div>
            </ModalVisibleContext.Provider>
        )
    }
}

export default Overview;
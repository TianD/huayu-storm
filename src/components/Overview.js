import React, { Component } from 'react';
import { Cascader, List } from 'antd';
import MyCard from './MyCard';
import DetailView from './DetailView';
import { ModalVisibleContext } from '../context';
import axios from 'axios';

axios.defaults.baseURL = 'http://127.0.0.1:5000/api'

class Overview extends Component {
    constructor() {
        super()
        this.state = {
            visible: false,
            project: null,
            project_list: null,
        }
    }

    changeVisible = (flag) => {
        this.setState({
            visible: flag
        })
    }

    changeProject = (value) => {
        this.setState({
            project: value
        })
    }

    changeProjectList = (value) => {
        console.log(value)
        this.setState({
            project_list: value
        })
    }

    componentDidMount() {
        axios.get('/get_project_list')
            .then((response) => {
                this.changeProjectList(response.data)
            })
    }

    render() {
        let { visible, project_list, project } = this.state;
        return (
            <ModalVisibleContext.Provider
                value={
                    {
                        visible: visible,
                        project_list: project_list,
                        project: project,
                        changeVisible: this.changeVisible,
                        changeProjectList: this.changeProjectList,
                        changeProject: this.changeProject
                    }
                }>
                <div>
                    <Cascader
                        options={project_list}
                        onChange={(value) => this.changeProject(value)}
                        placeholder="Please select" />
                    <List
                        itemLayout={'horizontal'}
                        dataSource={[1, 2, 3, 4, 66, 88, 8, 8, 8, 8, 8, 8, 8]}
                        grid={{ gutter: 24, lg: 3, md: 2, sm: 1, xs: 1 }}
                        column={4}
                        renderItem={
                            item => (
                                <MyCard onClick={(event) => this.changeVisible(true)} />
                            )
                        }
                    >
                    </List>
                    <DetailView visible={visible} />
                </div>
            </ModalVisibleContext.Provider>
        )
    }
}

export default Overview;
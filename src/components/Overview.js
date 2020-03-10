import React, {Component} from 'react';
import {Cascader, List} from 'antd';
import MyCard from './MyCard';
import DetailView from './DetailView';
import {ModalVisibleContext} from '../context';


const options = [
    {
        value: 'project1',
        label: 'Project1',
        children: [
            {
                value: 'ep01',
                label: 'ep01',
                children: [
                    {
                        value: 'se01',
                        label: 'se01',
                    },
                ],
            },
        ],
    },
    {
        value: 'project2',
        label: 'Project2',
        children: [
            {
                value: 'ep01',
                label: 'ep01',
                children: [
                    {
                        value: 'se01',
                        label: 'se01',
                    },
                ],
            },
        ],
    },
];

class Overview extends Component {
    constructor() {
        super()
        this.state = {
            visible: false,
        }
    }

    changeVisible = (flag) => {
        this.setState({
            visible: flag
        })
    }

    onChange = (value) => {
        console.log(value);
    }

    render() {
        let visible = this.state.visible;
        return (
            <ModalVisibleContext.Provider value={{visible: visible, changeVisible: this.changeVisible}}>
                <div>
                    <Cascader options={options} onChange={(value) => {
                        this.onChange(value)
                    }} placeholder="Please select"/>
                    <List
                        itemLayout={'horizontal'}
                        dataSource={[1, 2, 3, 4, 66, 88, 8, 8, 8, 8, 8, 8, 8]}
                        grid={{gutter: 24, lg: 3, md: 2, sm: 1, xs: 1}}
                        column={4}
                        renderItem={
                            item => (
                                <MyCard onClick={(event) => this.changeVisible(true)}/>
                            )
                        }
                    >
                    </List>
                    <DetailView visible={visible}/>
                </div>
            </ModalVisibleContext.Provider>
        )
    }
}

export default Overview;
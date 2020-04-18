import React, { Component } from 'react';
import { connect } from "react-redux";
import './App.css';
import { Layout, Menu } from 'antd';
import Overview from './components/Overview';
import BatchTableForMaya from './batchview/BatchTableForMaya';
import BatchTableForNuke from './batchview/BatchTableForNuke';
import BatchTableForSeqToMov from './batchview/BatchTableForSeqToMov';
import Logo from './logo.png';
import { get_project_list } from './actions/get_project_list'
import { set_nukebatch_items } from './actions/nukebatch';
import { set_seq2movbatch_items } from './actions/seq2movbatch';
import { set_mayabatch_items } from './actions/mayabatch';
import io from 'socket.io-client';

const socket = io('ws://localhost:8001')


const { Header, Content, Footer } = Layout;

function mapStateToProps(state) {
    return {
        nukebatch_items: state.nukebatch_items,
        seq2movbatch_items: state.seq2movbatch_items,
        mayabatch_items: state.mayabatch_items
    }
}

function mapDispatchToProps(dispatch) {
    return {
        get_project_list: () => dispatch(get_project_list()),
        set_nukebatch_items: (data) => dispatch(set_nukebatch_items(data)),
        set_seq2movbatch_items: (data) => dispatch(set_seq2movbatch_items(data)),
        set_mayabatch_items: (data) => dispatch(set_mayabatch_items(data))
    }
}

class App extends Component {

    constructor(props) {
        super(props)
        this.state = {
            page: '1',
        }
    }

    onChange(event) {
        this.setState(
            { page: event.key }
        )
    }

    componentDidMount() {
        this.mounted = true;
        this.props.get_project_list()
        socket.on('refresh_ui', data => {
            let view = data.view;
            switch (view) {
                case 'nukebatch':
                    let nukebatch_items = this.props.nukebatch_items;
                    let new_nukebatch_items = nukebatch_items.map((item) => {
                        if (item.key === data.key) {
                            return { ...item, status: data.status }
                        }
                        return item
                    })
                    if (this.mounted) {
                        this.props.set_nukebatch_items(new_nukebatch_items)
                    }
                    console.log('nukebatch refresh')
                    break
                case 'mayabatch':
                    let mayabatch_items = this.props.mayabatch_items;
                    let new_mayabatch_items = mayabatch_items.map((item) => {
                        if (item.key === data.key) {
                            return { ...item, status: data.status }
                        }
                        return item
                    })
                    if (this.mounted) {
                        this.props.set_mayabatch_items(new_mayabatch_items)
                    }
                    console.log('mayabatch refresh')
                    break
                case 'seq2movbatch':
                    let seq2movbatch_items = this.props.seq2movbatch_items;
                    let new_seq2movbatch_items = seq2movbatch_items.map((item) => {
                        if (item.key === data.key) {
                            return { ...item, status: data.status }
                        }
                        return item
                    })
                    if (this.mounted) {
                        this.props.set_seq2movbatch_items(new_seq2movbatch_items)
                    }
                    console.log('seq2movbatch refresh')
                    break
                default:
                    console.log('do nothing')
            }
        })
    }

    render() {
        let current_key = this.state.page;
        let current_page;
        switch (current_key) {
            case "1":
                current_page = <Overview />
                break
            case "2":
                current_page = <BatchTableForMaya />
                break
            case "3":
                current_page = <BatchTableForNuke />
                break
            case "4":
                current_page = <BatchTableForSeqToMov />
                break
            default:
                current_page = <Overview />
        }

        return (
            <div className="App">
                <Layout className="layout">
                    <Header>
                        <div className="logo" />

                        <Menu
                            theme="dark"
                            mode="horizontal"
                            defaultSelectedKeys={[current_key]}
                            style={{ lineHeight: '64px' }}
                            onClick={(value) => this.onChange(value)}
                        >
                            <Menu.Item key="1">Compositing</Menu.Item>
                            <Menu.Item key="2">Maya批处理</Menu.Item>
                            <Menu.Item key="3">Nuke模板</Menu.Item>
                            <Menu.Item key="4">序列转视频</Menu.Item>
                        </Menu>
                    </Header>
                    <Content style={{ padding: '20px 50px' }}>
                        <div className="site-layout-content">
                            {current_page}
                        </div>
                    </Content>
                    <Footer style={{ textAlign: 'center' }}><img src={Logo} height="10%" width="10%" alt="" /></Footer>
                </Layout>
            </div>
        );
    }

}

export default connect(mapStateToProps, mapDispatchToProps)(App);

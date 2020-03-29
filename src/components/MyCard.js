import React, { Component } from 'react';
import { Card } from 'antd';
import api from '../api'

const { Meta } = Card;

class MyCard extends Component {

    componentDidMount() {

    }

    render() {
        return (
            <Card
                hoverable
                style={{ width: 300, margin: (10, 10, 10, 10) }}
                type={"inner"}
                cover={
                    <img
                        alt="example"
                        src={api.get_thumbnail_url(this.props.shot)}
                    />
                }
                onClick={(event) => this.props.onClick(event)}
            >
                <Meta title={this.props.shot["label"]}/>
            </Card>
        )
    }
}

export default MyCard
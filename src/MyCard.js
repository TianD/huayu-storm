import React, { Component } from 'react';
import { Card } from 'antd';


const { Meta } = Card;

class MyCard extends Component {
    render() {
        return (
            <Card
                hoverable
                style={{ width: 240 }}
                cover={<img alt="example" src="https://os.alipayobjects.com/rmsportal/QBnOOoLaAfKPirc.png" />}
                onClick={(event)=>this.props.onClick(event)}
            >
                <Meta title="Europe Street beat" description="www.instagram.com" />
            </Card>
        )
    }
}

export default MyCard